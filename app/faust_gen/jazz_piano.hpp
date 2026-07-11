/* ------------------------------------------------------------
name: "jazz_piano"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn JazzPiano -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __JazzPiano_H__
#define  __JazzPiano_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS JazzPiano
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

class JazzPianoSIG0 {
	
  private:
	
	int iVec3[2];
	int iRec8[2];
	
  public:
	
	int getNumInputsJazzPianoSIG0() {
		return 0;
	}
	int getNumOutputsJazzPianoSIG0() {
		return 1;
	}
	
	void instanceInitJazzPianoSIG0(int sample_rate) {
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			iVec3[l10] = 0;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			iRec8[l11] = 0;
		}
	}
	
	void fillJazzPianoSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec3[0] = 1;
			iRec8[0] = (iVec3[1] + iRec8[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec8[0]));
			iVec3[1] = iVec3[0];
			iRec8[1] = iRec8[0];
		}
	}

};

static JazzPianoSIG0* newJazzPianoSIG0() { return (JazzPianoSIG0*)new JazzPianoSIG0(); }
static void deleteJazzPianoSIG0(JazzPianoSIG0* dsp) { delete dsp; }

static float JazzPiano_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0JazzPianoSIG0[65536];

class JazzPiano : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst5;
	FAUSTFLOAT fHslider0;
	float fConst6;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec2[2];
	float fConst7;
	float fConst8;
	float fConst9;
	int iRec3[2];
	FAUSTFLOAT fHslider1;
	float fRec1[3];
	int iRec4[2];
	float fConst10;
	float fRec5[2];
	float fConst11;
	float fConst12;
	FAUSTFLOAT fHslider2;
	float fConst13;
	float fConst15;
	float fConst16;
	float fRec7[2];
	int IOTA0;
	float fVec2[8192];
	float fRec6[3];
	float fConst17;
	float fConst18;
	float fRec9[2];
	FAUSTFLOAT fHslider3;
	float fConst19;
	float fConst20;
	float fRec10[2];
	float fConst21;
	float fConst22;
	float fRec11[2];
	float fConst23;
	float fConst24;
	float fRec12[2];
	float fConst25;
	float fConst26;
	float fRec13[2];
	float fConst27;
	float fConst28;
	float fRec14[2];
	float fConst29;
	float fConst30;
	float fRec15[2];
	float fConst31;
	float fConst32;
	float fRec16[2];
	float fConst33;
	float fRec17[2];
	FAUSTFLOAT fHslider4;
	float fRec0[3];
	
 public:
	JazzPiano() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn JazzPiano -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
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
		m->declare("filename", "jazz_piano.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
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
		m->declare("name", "jazz_piano");
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
		JazzPianoSIG0* sig0 = newJazzPianoSIG0();
		sig0->instanceInitJazzPianoSIG0(sample_rate);
		sig0->fillJazzPianoSIG0(65536, ftbl0JazzPianoSIG0);
		deleteJazzPianoSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(20420.352f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / JazzPiano_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -1.4142135f) / fConst1 + 1.0f;
		fConst5 = 1.0f / ((fConst3 + 1.4142135f) / fConst1 + 1.0f);
		fConst6 = 3.1415927f / fConst0;
		fConst7 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst8 = 1.0f / fConst7;
		fConst9 = 1.0f / std::max<float>(1.0f, 0.02f * fConst0);
		fConst10 = 1.0f / std::max<float>(1.0f, 0.18f * fConst0);
		fConst11 = std::max<float>(1.0f, 0.004f * fConst0);
		fConst12 = 1.0f / fConst11;
		fConst13 = 1.0f / std::max<float>(1.0f, 0.006f * fConst0);
		float fConst14 = 1.0f / std::tan(8168.141f / fConst0);
		fConst15 = 1.0f - fConst14;
		fConst16 = 1.0f / (fConst14 + 1.0f);
		fConst17 = 0.1724138f * fConst0;
		fConst18 = 9.144638f / fConst0;
		fConst19 = 0.1923077f * fConst0;
		fConst20 = 8.101753f / fConst0;
		fConst21 = 0.2173913f * fConst0;
		fConst22 = 7.0682673f / fConst0;
		fConst23 = 0.25f * fConst0;
		fConst24 = 6.0430455f / fConst0;
		fConst25 = 0.29411766f * fConst0;
		fConst26 = 5.0249376f / fConst0;
		fConst27 = 0.35714287f * fConst0;
		fConst28 = 4.0127797f / fConst0;
		fConst29 = 0.45454547f * fConst0;
		fConst30 = 3.0053952f / fConst0;
		fConst31 = 0.625f * fConst0;
		fConst32 = 2.0015993f / fConst0;
		fConst33 = 1.0002f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(2.2e+02f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.4f);
		fHslider2 = FAUSTFLOAT(2.0f);
		fHslider3 = FAUSTFLOAT(0.5f);
		fHslider4 = FAUSTFLOAT(0.8f);
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
			iRec3[l3] = 0;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec1[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec4[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec5[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec7[l7] = 0.0f;
		}
		IOTA0 = 0;
		for (int l8 = 0; l8 < 8192; l8 = l8 + 1) {
			fVec2[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 3; l9 = l9 + 1) {
			fRec6[l9] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec9[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fRec10[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 2; l14 = l14 + 1) {
			fRec11[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 2; l15 = l15 + 1) {
			fRec12[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 2; l16 = l16 + 1) {
			fRec13[l16] = 0.0f;
		}
		for (int l17 = 0; l17 < 2; l17 = l17 + 1) {
			fRec14[l17] = 0.0f;
		}
		for (int l18 = 0; l18 < 2; l18 = l18 + 1) {
			fRec15[l18] = 0.0f;
		}
		for (int l19 = 0; l19 < 2; l19 = l19 + 1) {
			fRec16[l19] = 0.0f;
		}
		for (int l20 = 0; l20 < 2; l20 = l20 + 1) {
			fRec17[l20] = 0.0f;
		}
		for (int l21 = 0; l21 < 3; l21 = l21 + 1) {
			fRec0[l21] = 0.0f;
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
	
	virtual JazzPiano* clone() {
		return new JazzPiano();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("jazz_piano");
		ui_interface->addHorizontalSlider("brightness", &fHslider3, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("decay", &fHslider2, FAUSTFLOAT(2.0f), FAUSTFLOAT(0.4f), FAUSTFLOAT(4.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("felt", &fHslider1, FAUSTFLOAT(0.4f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider0, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = std::tan(fConst6 * (2.5f * fSlow0 + 1.8e+03f));
		float fSlow2 = 2.0f * (1.0f - 1.0f / JazzPiano_faustpower2_f(fSlow1));
		float fSlow3 = 1.0f / fSlow1;
		float fSlow4 = (fSlow3 + -1.4142135f) / fSlow1 + 1.0f;
		float fSlow5 = (fSlow3 + 1.4142135f) / fSlow1 + 1.0f;
		float fSlow6 = 1.0f / fSlow5;
		float fSlow7 = float(fButton0);
		float fSlow8 = 4.656613e-10f * float(fHslider1);
		float fSlow9 = 0.45f / fSlow5;
		int iSlow10 = fSlow7 == 0.0f;
		float fSlow11 = float(fHslider2);
		float fSlow12 = 1.0f / std::max<float>(1.0f, fConst0 * fSlow11);
		float fSlow13 = fConst0 / fSlow0;
		float fSlow14 = fSlow13 + -2.499995f;
		int iSlow15 = int(fSlow14);
		int iSlow16 = std::min<int>(4096, std::max<int>(0, iSlow15 + 4));
		float fSlow17 = std::floor(fSlow14);
		float fSlow18 = fSlow13 + (-4.0f - fSlow17);
		float fSlow19 = fSlow13 + (-3.0f - fSlow17);
		float fSlow20 = fSlow13 + (-2.0f - fSlow17);
		float fSlow21 = fSlow13 + (-1.0f - fSlow17);
		float fSlow22 = fSlow21 * fSlow20;
		float fSlow23 = fSlow22 * fSlow19;
		float fSlow24 = 0.041666668f * fSlow23 * fSlow18;
		int iSlow25 = std::min<int>(4096, std::max<int>(0, iSlow15 + 3));
		float fSlow26 = 0.16666667f * fSlow23;
		int iSlow27 = std::min<int>(4096, std::max<int>(0, iSlow15 + 2));
		float fSlow28 = 0.25f * fSlow22;
		int iSlow29 = std::min<int>(4096, std::max<int>(0, iSlow15 + 1));
		float fSlow30 = 0.16666667f * fSlow21;
		int iSlow31 = std::min<int>(4096, std::max<int>(0, iSlow15));
		float fSlow32 = 0.041666668f * fSlow20;
		float fSlow33 = fSlow13 + (-5.0f - fSlow17);
		float fSlow34 = 1.0f / std::max<float>(1.0f, fConst17 * fSlow11);
		float fSlow35 = fConst18 * fSlow0;
		float fSlow36 = 1.6f - 1.15f * float(fHslider3);
		float fSlow37 = std::pow(9.0f, -fSlow36);
		float fSlow38 = 1.0f / std::max<float>(1.0f, fConst19 * fSlow11);
		float fSlow39 = fConst20 * fSlow0;
		float fSlow40 = std::pow(8.0f, -fSlow36);
		float fSlow41 = 1.0f / std::max<float>(1.0f, fConst21 * fSlow11);
		float fSlow42 = fConst22 * fSlow0;
		float fSlow43 = std::pow(7.0f, -fSlow36);
		float fSlow44 = 1.0f / std::max<float>(1.0f, fConst23 * fSlow11);
		float fSlow45 = fConst24 * fSlow0;
		float fSlow46 = std::pow(6.0f, -fSlow36);
		float fSlow47 = 1.0f / std::max<float>(1.0f, fConst25 * fSlow11);
		float fSlow48 = fConst26 * fSlow0;
		float fSlow49 = std::pow(5.0f, -fSlow36);
		float fSlow50 = 1.0f / std::max<float>(1.0f, fConst27 * fSlow11);
		float fSlow51 = fConst28 * fSlow0;
		float fSlow52 = std::pow(4.0f, -fSlow36);
		float fSlow53 = 1.0f / std::max<float>(1.0f, fConst29 * fSlow11);
		float fSlow54 = fConst30 * fSlow0;
		float fSlow55 = std::pow(3.0f, -fSlow36);
		float fSlow56 = 1.0f / std::max<float>(1.0f, fConst31 * fSlow11);
		float fSlow57 = fConst32 * fSlow0;
		float fSlow58 = std::pow(2.0f, -fSlow36);
		float fSlow59 = fConst33 * fSlow0;
		float fSlow60 = std::pow(1.0f, -fSlow36);
		float fSlow61 = float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow7;
			iRec2[0] = (iRec2[1] + (iRec2[1] > 0)) * (fSlow7 <= fVec1[1]) + (fSlow7 > fVec1[1]);
			float fTemp0 = float(iRec2[0]);
			float fTemp1 = fConst8 * fTemp0;
			float fTemp2 = fConst7 - fTemp0;
			iRec3[0] = 1103515245 * iRec3[1] + 12345;
			float fTemp3 = float(iRec3[0]);
			fRec1[0] = fSlow8 * fTemp3 * std::max<float>(0.0f, std::min<float>(fTemp1, fConst9 * fTemp2 + 1.0f)) - fSlow6 * (fSlow4 * fRec1[2] + fSlow2 * fRec1[1]);
			iRec4[0] = iSlow10 * (iRec4[1] + 1);
			float fTemp4 = 1.0f - fConst10 * float(iRec4[0]);
			fRec5[0] = fSlow7 + fRec5[1] * float(fVec1[1] >= fSlow7);
			float fTemp5 = fConst12 * fRec5[0];
			float fTemp6 = fConst11 - fRec5[0];
			float fTemp7 = std::max<float>(0.0f, std::min<float>(fTemp5, std::max<float>(fSlow12 * fTemp6 + 1.0f, 0.0f)) * fTemp4);
			fRec7[0] = -(fConst16 * (fConst15 * fRec7[1] - (fRec6[1] + fRec6[2])));
			float fTemp8 = 0.988f * fRec7[0] + 4.656613e-10f * fTemp3 * std::max<float>(0.0f, std::min<float>(fTemp1, fConst13 * fTemp2 + 1.0f));
			fVec2[IOTA0 & 8191] = fTemp8;
			fRec6[0] = fSlow33 * (fSlow18 * (fSlow19 * (fSlow32 * fVec2[(IOTA0 - iSlow31) & 8191] - fSlow30 * fVec2[(IOTA0 - iSlow29) & 8191]) + fSlow28 * fVec2[(IOTA0 - iSlow27) & 8191]) - fSlow26 * fVec2[(IOTA0 - iSlow25) & 8191]) + fSlow24 * fVec2[(IOTA0 - iSlow16) & 8191];
			int iTemp9 = 1 - iVec0[1];
			float fTemp10 = ((iTemp9) ? 0.0f : fSlow35 + fRec9[1]);
			fRec9[0] = fTemp10 - std::floor(fTemp10);
			float fTemp11 = ((iTemp9) ? 0.0f : fSlow39 + fRec10[1]);
			fRec10[0] = fTemp11 - std::floor(fTemp11);
			float fTemp12 = ((iTemp9) ? 0.0f : fSlow42 + fRec11[1]);
			fRec11[0] = fTemp12 - std::floor(fTemp12);
			float fTemp13 = ((iTemp9) ? 0.0f : fSlow45 + fRec12[1]);
			fRec12[0] = fTemp13 - std::floor(fTemp13);
			float fTemp14 = ((iTemp9) ? 0.0f : fSlow48 + fRec13[1]);
			fRec13[0] = fTemp14 - std::floor(fTemp14);
			float fTemp15 = ((iTemp9) ? 0.0f : fSlow51 + fRec14[1]);
			fRec14[0] = fTemp15 - std::floor(fTemp15);
			float fTemp16 = ((iTemp9) ? 0.0f : fSlow54 + fRec15[1]);
			fRec15[0] = fTemp16 - std::floor(fTemp16);
			float fTemp17 = ((iTemp9) ? 0.0f : fSlow57 + fRec16[1]);
			fRec16[0] = fTemp17 - std::floor(fTemp17);
			float fTemp18 = ((iTemp9) ? 0.0f : fSlow59 + fRec17[1]);
			fRec17[0] = fTemp18 - std::floor(fTemp18);
			fRec0[0] = fSlow61 * (0.28f * (fSlow60 * ftbl0JazzPianoSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec17[0]), 65535))] * fTemp7 + fSlow58 * ftbl0JazzPianoSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec16[0]), 65535))] * std::max<float>(0.0f, fTemp4 * std::min<float>(fTemp5, std::max<float>(fSlow56 * fTemp6 + 1.0f, 0.0f))) + fSlow55 * ftbl0JazzPianoSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec15[0]), 65535))] * std::max<float>(0.0f, fTemp4 * std::min<float>(fTemp5, std::max<float>(fSlow53 * fTemp6 + 1.0f, 0.0f))) + fSlow52 * ftbl0JazzPianoSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec14[0]), 65535))] * std::max<float>(0.0f, fTemp4 * std::min<float>(fTemp5, std::max<float>(fSlow50 * fTemp6 + 1.0f, 0.0f))) + fSlow49 * ftbl0JazzPianoSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec13[0]), 65535))] * std::max<float>(0.0f, fTemp4 * std::min<float>(fTemp5, std::max<float>(fSlow47 * fTemp6 + 1.0f, 0.0f))) + fSlow46 * ftbl0JazzPianoSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec12[0]), 65535))] * std::max<float>(0.0f, fTemp4 * std::min<float>(fTemp5, std::max<float>(fSlow44 * fTemp6 + 1.0f, 0.0f))) + fSlow43 * ftbl0JazzPianoSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec11[0]), 65535))] * std::max<float>(0.0f, fTemp4 * std::min<float>(fTemp5, std::max<float>(fSlow41 * fTemp6 + 1.0f, 0.0f))) + fSlow40 * ftbl0JazzPianoSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec10[0]), 65535))] * std::max<float>(0.0f, fTemp4 * std::min<float>(fTemp5, std::max<float>(fSlow38 * fTemp6 + 1.0f, 0.0f))) + fSlow37 * ftbl0JazzPianoSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec9[0]), 65535))] * std::max<float>(0.0f, fTemp4 * std::min<float>(fTemp5, std::max<float>(fSlow34 * fTemp6 + 1.0f, 0.0f)))) + 0.2f * fRec6[0] * fTemp7 + fSlow9 * (fRec1[2] + fRec1[0] + 2.0f * fRec1[1])) - fConst5 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			float fTemp19 = tanhf(fConst5 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]));
			output0[i0] = FAUSTFLOAT(fTemp19);
			output1[i0] = FAUSTFLOAT(fTemp19);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec2[1] = iRec2[0];
			iRec3[1] = iRec3[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			iRec4[1] = iRec4[0];
			fRec5[1] = fRec5[0];
			fRec7[1] = fRec7[0];
			IOTA0 = IOTA0 + 1;
			fRec6[2] = fRec6[1];
			fRec6[1] = fRec6[0];
			fRec9[1] = fRec9[0];
			fRec10[1] = fRec10[0];
			fRec11[1] = fRec11[0];
			fRec12[1] = fRec12[0];
			fRec13[1] = fRec13[0];
			fRec14[1] = fRec14[0];
			fRec15[1] = fRec15[0];
			fRec16[1] = fRec16[0];
			fRec17[1] = fRec17[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
