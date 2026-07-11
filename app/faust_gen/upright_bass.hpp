/* ------------------------------------------------------------
name: "upright_bass"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn UprightBass -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __UprightBass_H__
#define  __UprightBass_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS UprightBass
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

class UprightBassSIG0 {
	
  private:
	
	int iVec4[2];
	int iRec13[2];
	
  public:
	
	int getNumInputsUprightBassSIG0() {
		return 0;
	}
	int getNumOutputsUprightBassSIG0() {
		return 1;
	}
	
	void instanceInitUprightBassSIG0(int sample_rate) {
		for (int l15 = 0; l15 < 2; l15 = l15 + 1) {
			iVec4[l15] = 0;
		}
		for (int l16 = 0; l16 < 2; l16 = l16 + 1) {
			iRec13[l16] = 0;
		}
	}
	
	void fillUprightBassSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec4[0] = 1;
			iRec13[0] = (iVec4[1] + iRec13[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec13[0]));
			iVec4[1] = iVec4[0];
			iRec13[1] = iRec13[0];
		}
	}

};

static UprightBassSIG0* newUprightBassSIG0() { return (UprightBassSIG0*)new UprightBassSIG0(); }
static void deleteUprightBassSIG0(UprightBassSIG0* dsp) { delete dsp; }

static float UprightBass_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0UprightBassSIG0[65536];

class UprightBass : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst6;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec2[2];
	float fConst7;
	float fRec3[2];
	float fConst8;
	float fConst9;
	FAUSTFLOAT fHslider0;
	float fConst11;
	float fConst13;
	float fConst15;
	float fConst18;
	int iRec6[2];
	float fConst19;
	float fConst20;
	float fConst21;
	int iRec7[2];
	float fVec2[2];
	float fConst22;
	float fConst23;
	float fRec5[2];
	float fRec4[3];
	FAUSTFLOAT fHslider1;
	float fConst24;
	float fConst26;
	float fConst28;
	float fConst30;
	float fConst31;
	float fConst32;
	float fConst33;
	float fConst35;
	float fConst36;
	float fRec10[2];
	int IOTA0;
	float fVec3[16384];
	FAUSTFLOAT fHslider2;
	float fRec9[3];
	float fRec8[3];
	float fConst37;
	float fConst39;
	float fConst41;
	float fConst43;
	float fRec11[3];
	float fConst44;
	float fConst46;
	float fConst48;
	float fConst50;
	float fRec12[3];
	float fConst51;
	FAUSTFLOAT fHslider3;
	float fConst52;
	float fRec14[2];
	float fVec5[2];
	float fConst53;
	float fConst54;
	float fRec1[2];
	float fRec0[3];
	FAUSTFLOAT fHslider4;
	float fConst55;
	
 public:
	UprightBass() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn UprightBass -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/fdelay4:author", "Julius O. Smith III");
		m->declare("delays.lib/fdelayltv:author", "Julius O. Smith III");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "upright_bass.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "upright_bass");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		UprightBassSIG0* sig0 = newUprightBassSIG0();
		sig0->instanceInitUprightBassSIG0(sample_rate);
		sig0->fillUprightBassSIG0(65536, ftbl0UprightBassSIG0);
		deleteUprightBassSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(8482.3f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / UprightBass_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -1.0f) / fConst1 + 1.0f;
		float fConst5 = (fConst3 + 1.0f) / fConst1 + 1.0f;
		fConst6 = 1.0f / fConst5;
		fConst7 = 1.0f / std::max<float>(1.0f, 0.06f * fConst0);
		fConst8 = std::max<float>(1.0f, 0.003f * fConst0);
		fConst9 = 1.0f / fConst8;
		float fConst10 = std::tan(10053.097f / fConst0);
		fConst11 = 2.0f * (1.0f - 1.0f / UprightBass_faustpower2_f(fConst10));
		float fConst12 = 1.0f / fConst10;
		fConst13 = (fConst12 + -1.4142135f) / fConst10 + 1.0f;
		float fConst14 = (fConst12 + 1.4142135f) / fConst10 + 1.0f;
		fConst15 = 1.0f / fConst14;
		float fConst16 = std::tan(2199.1147f / fConst0);
		float fConst17 = 1.0f / fConst16;
		fConst18 = 1.0f - fConst17;
		fConst19 = std::max<float>(1.0f, 0.0003f * fConst0);
		fConst20 = 1.0f / fConst19;
		fConst21 = 1.0f / std::max<float>(1.0f, 0.015f * fConst0);
		fConst22 = 4.656613e-10f / fConst16;
		fConst23 = 1.0f / (fConst17 + 1.0f);
		fConst24 = 0.6f / fConst14;
		float fConst25 = std::tan(753.98224f / fConst0);
		fConst26 = 2.0f * (1.0f - 1.0f / UprightBass_faustpower2_f(fConst25));
		float fConst27 = 1.0f / fConst25;
		fConst28 = (fConst27 + -0.2f) / fConst25 + 1.0f;
		float fConst29 = (fConst27 + 0.2f) / fConst25 + 1.0f;
		fConst30 = 1.0f / fConst29;
		fConst31 = std::max<float>(1.0f, 0.0004f * fConst0);
		fConst32 = 1.0f / fConst31;
		fConst33 = 1.0f / std::max<float>(1.0f, 0.006f * fConst0);
		float fConst34 = 1.0f / std::tan(7539.8223f / fConst0);
		fConst35 = 1.0f - fConst34;
		fConst36 = 1.0f / (fConst34 + 1.0f);
		fConst37 = 0.65f / (fConst25 * fConst29);
		float fConst38 = std::tan(439.82297f / fConst0);
		fConst39 = 2.0f * (1.0f - 1.0f / UprightBass_faustpower2_f(fConst38));
		float fConst40 = 1.0f / fConst38;
		fConst41 = (fConst40 + -0.14285715f) / fConst38 + 1.0f;
		float fConst42 = (fConst40 + 0.14285715f) / fConst38 + 1.0f;
		fConst43 = 1.0f / fConst42;
		fConst44 = 0.95f / (fConst38 * fConst42);
		float fConst45 = std::tan(235.61945f / fConst0);
		fConst46 = 2.0f * (1.0f - 1.0f / UprightBass_faustpower2_f(fConst45));
		float fConst47 = 1.0f / fConst45;
		fConst48 = (fConst47 + -0.11111111f) / fConst45 + 1.0f;
		float fConst49 = (fConst47 + 0.11111111f) / fConst45 + 1.0f;
		fConst50 = 1.0f / fConst49;
		fConst51 = 1.0f / (fConst45 * fConst49);
		fConst52 = 1.0f / fConst0;
		fConst53 = 1.0f - fConst3;
		fConst54 = 1.0f / (fConst3 + 1.0f);
		fConst55 = 0.5f / fConst5;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(1.0f);
		fHslider1 = FAUSTFLOAT(0.5f);
		fHslider2 = FAUSTFLOAT(55.0f);
		fHslider3 = FAUSTFLOAT(0.6f);
		fHslider4 = FAUSTFLOAT(0.85f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec2[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec3[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec6[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec7[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fVec2[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec5[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 3; l8 = l8 + 1) {
			fRec4[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec10[l9] = 0.0f;
		}
		IOTA0 = 0;
		for (int l10 = 0; l10 < 16384; l10 = l10 + 1) {
			fVec3[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 3; l11 = l11 + 1) {
			fRec9[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 3; l12 = l12 + 1) {
			fRec8[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 3; l13 = l13 + 1) {
			fRec11[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 3; l14 = l14 + 1) {
			fRec12[l14] = 0.0f;
		}
		for (int l17 = 0; l17 < 2; l17 = l17 + 1) {
			fRec14[l17] = 0.0f;
		}
		for (int l18 = 0; l18 < 2; l18 = l18 + 1) {
			fVec5[l18] = 0.0f;
		}
		for (int l19 = 0; l19 < 2; l19 = l19 + 1) {
			fRec1[l19] = 0.0f;
		}
		for (int l20 = 0; l20 < 3; l20 = l20 + 1) {
			fRec0[l20] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual UprightBass* clone() {
		return new UprightBass();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("upright_bass");
		ui_interface->addHorizontalSlider("body", &fHslider3, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("click", &fHslider1, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(1.0f), FAUSTFLOAT(0.2f), FAUSTFLOAT(3.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(55.0f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.85f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow3 = fConst24 * float(fHslider1);
		float fSlow4 = float(fHslider2);
		float fSlow5 = fConst0 / fSlow4;
		float fSlow6 = fSlow5 + -2.499995f;
		int iSlow7 = int(fSlow6);
		int iSlow8 = std::min<int>(8192, std::max<int>(0, iSlow7 + 4));
		float fSlow9 = std::floor(fSlow6);
		float fSlow10 = fSlow5 + (-4.0f - fSlow9);
		float fSlow11 = fSlow5 + (-3.0f - fSlow9);
		float fSlow12 = fSlow5 + (-2.0f - fSlow9);
		float fSlow13 = fSlow5 + (-1.0f - fSlow9);
		float fSlow14 = fSlow13 * fSlow12;
		float fSlow15 = fSlow14 * fSlow11;
		float fSlow16 = 0.041666668f * fSlow15 * fSlow10;
		int iSlow17 = std::min<int>(8192, std::max<int>(0, iSlow7 + 3));
		float fSlow18 = 0.16666667f * fSlow15;
		int iSlow19 = std::min<int>(8192, std::max<int>(0, iSlow7 + 2));
		float fSlow20 = 0.25f * fSlow14;
		int iSlow21 = std::min<int>(8192, std::max<int>(0, iSlow7 + 1));
		float fSlow22 = 0.16666667f * fSlow13;
		int iSlow23 = std::min<int>(8192, std::max<int>(0, iSlow7));
		float fSlow24 = 0.041666668f * fSlow12;
		float fSlow25 = fSlow5 + (-5.0f - fSlow9);
		float fSlow26 = float(fHslider3);
		float fSlow27 = fConst52 * fSlow4;
		float fSlow28 = fConst55 * float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec2[0] = iSlow1 * (iRec2[1] + 1);
			fRec3[0] = fSlow0 + fRec3[1] * float(fVec1[1] >= fSlow0);
			iRec6[0] = (fSlow0 > fVec1[1]) + (fSlow0 <= fVec1[1]) * (iRec6[1] + (iRec6[1] > 0));
			float fTemp0 = float(iRec6[0]);
			iRec7[0] = 1103515245 * iRec7[1] + 12345;
			float fTemp1 = float(iRec7[0]);
			float fTemp2 = fTemp1 * std::max<float>(0.0f, std::min<float>(fConst20 * fTemp0, fConst21 * (fConst19 - fTemp0) + 1.0f));
			fVec2[0] = fTemp2;
			fRec5[0] = fConst23 * (fConst22 * (fTemp2 - fVec2[1]) - fConst18 * fRec5[1]);
			fRec4[0] = fRec5[0] - fConst15 * (fConst13 * fRec4[2] + fConst11 * fRec4[1]);
			fRec10[0] = -(fConst36 * (fConst35 * fRec10[1] - (fRec9[1] + fRec9[2])));
			float fTemp3 = 0.992f * fRec10[0] + 4.656613e-10f * fTemp1 * std::max<float>(0.0f, std::min<float>(fConst32 * fTemp0, fConst33 * (fConst31 - fTemp0) + 1.0f));
			fVec3[IOTA0 & 16383] = fTemp3;
			fRec9[0] = fSlow25 * (fSlow10 * (fSlow11 * (fSlow24 * fVec3[(IOTA0 - iSlow23) & 16383] - fSlow22 * fVec3[(IOTA0 - iSlow21) & 16383]) + fSlow20 * fVec3[(IOTA0 - iSlow19) & 16383]) - fSlow18 * fVec3[(IOTA0 - iSlow17) & 16383]) + fSlow16 * fVec3[(IOTA0 - iSlow8) & 16383];
			fRec8[0] = fRec9[0] - fConst30 * (fConst28 * fRec8[2] + fConst26 * fRec8[1]);
			fRec11[0] = fRec9[0] - fConst43 * (fConst41 * fRec11[2] + fConst39 * fRec11[1]);
			fRec12[0] = fRec9[0] - fConst50 * (fConst48 * fRec12[2] + fConst46 * fRec12[1]);
			float fTemp4 = ((1 - iVec0[1]) ? 0.0f : fSlow27 + fRec14[1]);
			fRec14[0] = fTemp4 - std::floor(fTemp4);
			float fTemp5 = (fRec9[0] + 0.35f * ftbl0UprightBassSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec14[0]), 65535))] + fSlow26 * (fConst51 * (fRec12[0] - fRec12[2]) + fConst44 * (fRec11[0] - fRec11[2]) + fConst37 * (fRec8[0] - fRec8[2])) + fSlow3 * (fRec4[2] + fRec4[0] + 2.0f * fRec4[1])) * std::max<float>(0.0f, std::min<float>(fConst9 * fRec3[0], std::max<float>(fSlow2 * (fConst8 - fRec3[0]) + 1.0f, 0.0f)) * (1.0f - fConst7 * float(iRec2[0])));
			fVec5[0] = fTemp5;
			fRec1[0] = -(fConst54 * (fConst53 * fRec1[1] - (fTemp5 + fVec5[1])));
			fRec0[0] = fRec1[0] - fConst6 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			float fTemp6 = fSlow28 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp6);
			output1[i0] = FAUSTFLOAT(fTemp6);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec2[1] = iRec2[0];
			fRec3[1] = fRec3[0];
			iRec6[1] = iRec6[0];
			iRec7[1] = iRec7[0];
			fVec2[1] = fVec2[0];
			fRec5[1] = fRec5[0];
			fRec4[2] = fRec4[1];
			fRec4[1] = fRec4[0];
			fRec10[1] = fRec10[0];
			IOTA0 = IOTA0 + 1;
			fRec9[2] = fRec9[1];
			fRec9[1] = fRec9[0];
			fRec8[2] = fRec8[1];
			fRec8[1] = fRec8[0];
			fRec11[2] = fRec11[1];
			fRec11[1] = fRec11[0];
			fRec12[2] = fRec12[1];
			fRec12[1] = fRec12[0];
			fRec14[1] = fRec14[0];
			fVec5[1] = fVec5[0];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
