/* ------------------------------------------------------------
name: "mbira"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Mbira -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Mbira_H__
#define  __Mbira_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Mbira
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

class MbiraSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec8[2];
	
  public:
	
	int getNumInputsMbiraSIG0() {
		return 0;
	}
	int getNumOutputsMbiraSIG0() {
		return 1;
	}
	
	void instanceInitMbiraSIG0(int sample_rate) {
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			iVec2[l9] = 0;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			iRec8[l10] = 0;
		}
	}
	
	void fillMbiraSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec8[0] = (iVec2[1] + iRec8[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec8[0]));
			iVec2[1] = iVec2[0];
			iRec8[1] = iRec8[0];
		}
	}

};

static MbiraSIG0* newMbiraSIG0() { return (MbiraSIG0*)new MbiraSIG0(); }
static void deleteMbiraSIG0(MbiraSIG0* dsp) { delete dsp; }

static float Mbira_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0MbiraSIG0[65536];

class Mbira : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst5;
	float fConst8;
	float fConst10;
	float fConst12;
	float fConst14;
	float fConst16;
	float fConst18;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec3[2];
	float fConst19;
	float fRec4[2];
	float fConst20;
	float fConst21;
	FAUSTFLOAT fHslider0;
	int iRec5[2];
	float fConst22;
	float fRec6[2];
	float fConst23;
	float fRec7[2];
	FAUSTFLOAT fHslider1;
	float fRec2[3];
	float fConst24;
	float fRec1[3];
	float fConst25;
	FAUSTFLOAT fHslider2;
	float fConst26;
	float fRec9[2];
	float fConst29;
	int iRec11[2];
	float fConst30;
	float fConst31;
	float fConst32;
	float fVec3[2];
	float fConst33;
	float fConst34;
	float fRec10[2];
	float fConst35;
	float fConst36;
	float fConst37;
	float fRec12[2];
	FAUSTFLOAT fHslider3;
	float fRec0[3];
	
 public:
	Mbira() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Mbira -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "mbira.dsp");
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
		m->declare("name", "mbira");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
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
		MbiraSIG0* sig0 = newMbiraSIG0();
		sig0->instanceInitMbiraSIG0(sample_rate);
		sig0->fillMbiraSIG0(65536, ftbl0MbiraSIG0);
		deleteMbiraSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(25132.742f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / Mbira_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -1.4142135f) / fConst1 + 1.0f;
		fConst5 = 1.0f / ((fConst3 + 1.4142135f) / fConst1 + 1.0f);
		float fConst6 = std::tan(5654.8667f / fConst0);
		float fConst7 = Mbira_faustpower2_f(fConst6);
		fConst8 = 2.0f * (1.0f - 1.0f / fConst7);
		float fConst9 = 1.0f / fConst6;
		fConst10 = (fConst9 + -1.4142135f) / fConst6 + 1.0f;
		float fConst11 = (fConst9 + 1.4142135f) / fConst6 + 1.0f;
		fConst12 = 1.0f / fConst11;
		float fConst13 = std::tan(10367.256f / fConst0);
		fConst14 = 2.0f * (1.0f - 1.0f / Mbira_faustpower2_f(fConst13));
		float fConst15 = 1.0f / fConst13;
		fConst16 = (fConst15 + -0.7692308f) / fConst13 + 1.0f;
		float fConst17 = (fConst15 + 0.7692308f) / fConst13 + 1.0f;
		fConst18 = 1.0f / fConst17;
		fConst19 = 1.0f / std::max<float>(1.0f, 0.12f * fConst0);
		fConst20 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst21 = 1.0f / fConst20;
		fConst22 = 87.0f / fConst0;
		fConst23 = 113.0f / fConst0;
		fConst24 = 1.0f / (fConst13 * fConst17);
		fConst25 = 1.0f / (fConst7 * fConst11);
		fConst26 = 1.0f / fConst0;
		float fConst27 = std::tan(4398.2295f / fConst0);
		float fConst28 = 1.0f / fConst27;
		fConst29 = 1.0f - fConst28;
		fConst30 = std::max<float>(1.0f, 0.0004f * fConst0);
		fConst31 = 1.0f / fConst30;
		fConst32 = 1.0f / std::max<float>(1.0f, 0.005f * fConst0);
		fConst33 = 1.1641532e-10f / fConst27;
		fConst34 = 1.0f / (fConst28 + 1.0f);
		fConst35 = 1.0f / std::max<float>(1.0f, 0.05f * fConst0);
		fConst36 = 1.0f / std::max<float>(1.0f, 0.11f * fConst0);
		fConst37 = 2.04f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.5f);
		fHslider1 = FAUSTFLOAT(0.55f);
		fHslider2 = FAUSTFLOAT(4.4e+02f);
		fHslider3 = FAUSTFLOAT(0.7f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec3[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec4[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec5[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec6[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec7[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 3; l7 = l7 + 1) {
			fRec2[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 3; l8 = l8 + 1) {
			fRec1[l8] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec9[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			iRec11[l12] = 0;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fVec3[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 2; l14 = l14 + 1) {
			fRec10[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 2; l15 = l15 + 1) {
			fRec12[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 3; l16 = l16 + 1) {
			fRec0[l16] = 0.0f;
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
	
	virtual Mbira* clone() {
		return new Mbira();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("mbira");
		ui_interface->addHorizontalSlider("buzz", &fHslider1, FAUSTFLOAT(0.55f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.1f), FAUSTFLOAT(1.6f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(4.4e+02f), FAUSTFLOAT(6e+01f), FAUSTFLOAT(3e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider3, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow3 = 3.259629e-10f * float(fHslider1);
		float fSlow4 = float(fHslider2);
		float fSlow5 = fConst26 * fSlow4;
		float fSlow6 = fConst37 * fSlow4;
		float fSlow7 = 0.5f * float(fHslider3);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec3[0] = iSlow1 * (iRec3[1] + 1);
			float fTemp0 = float(iRec3[0]);
			fRec4[0] = fSlow0 + fRec4[1] * float(fVec1[1] >= fSlow0);
			float fTemp1 = fConst21 * fRec4[0];
			float fTemp2 = fConst20 - fRec4[0];
			float fTemp3 = std::max<float>(0.0f, std::min<float>(fTemp1, std::max<float>(fSlow2 * fTemp2 + 1.0f, 0.0f)) * (1.0f - fConst19 * fTemp0));
			iRec5[0] = 1103515245 * iRec5[1] + 12345;
			float fTemp4 = float(iRec5[0]);
			int iTemp5 = 1 - iVec0[1];
			float fTemp6 = ((iTemp5) ? 0.0f : fConst22 + fRec6[1]);
			fRec6[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = ((iTemp5) ? 0.0f : fConst23 + fRec7[1]);
			fRec7[0] = fTemp7 - std::floor(fTemp7);
			fRec2[0] = fSlow3 * float((fRec7[0] < 0.4f) * (fRec6[0] < 0.55f)) * fTemp4 * Mbira_faustpower2_f(fTemp3) - fConst18 * (fConst16 * fRec2[2] + fConst14 * fRec2[1]);
			fRec1[0] = fConst24 * (fRec2[0] - fRec2[2]) - fConst12 * (fConst10 * fRec1[2] + fConst8 * fRec1[1]);
			float fTemp8 = ((iTemp5) ? 0.0f : fSlow5 + fRec9[1]);
			fRec9[0] = fTemp8 - std::floor(fTemp8);
			iRec11[0] = (iRec11[1] + (iRec11[1] > 0)) * (fSlow0 <= fVec1[1]) + (fSlow0 > fVec1[1]);
			float fTemp9 = float(iRec11[0]);
			float fTemp10 = fTemp4 * std::max<float>(0.0f, std::min<float>(fConst31 * fTemp9, fConst32 * (fConst30 - fTemp9) + 1.0f));
			fVec3[0] = fTemp10;
			fRec10[0] = fConst34 * (fConst33 * (fTemp10 - fVec3[1]) - fConst29 * fRec10[1]);
			float fTemp11 = ((iTemp5) ? 0.0f : fSlow6 + fRec12[1]);
			fRec12[0] = fTemp11 - std::floor(fTemp11);
			fRec0[0] = fSlow7 * (0.3f * ftbl0MbiraSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec12[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fTemp1, std::max<float>(fConst36 * fTemp2 + 1.0f, 0.0f)) * (1.0f - fConst35 * fTemp0)) + fRec10[0] + ftbl0MbiraSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec9[0]), 65535))] * fTemp3 + fConst25 * (fRec1[2] + (fRec1[0] - 2.0f * fRec1[1]))) - fConst5 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			float fTemp12 = fConst5 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp12);
			output1[i0] = FAUSTFLOAT(fTemp12);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec3[1] = iRec3[0];
			fRec4[1] = fRec4[0];
			iRec5[1] = iRec5[0];
			fRec6[1] = fRec6[0];
			fRec7[1] = fRec7[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec9[1] = fRec9[0];
			iRec11[1] = iRec11[0];
			fVec3[1] = fVec3[0];
			fRec10[1] = fRec10[0];
			fRec12[1] = fRec12[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
