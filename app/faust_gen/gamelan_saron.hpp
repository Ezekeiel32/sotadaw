/* ------------------------------------------------------------
name: "gamelan_saron"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn GamelanSaron -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __GamelanSaron_H__
#define  __GamelanSaron_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS GamelanSaron
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

class GamelanSaronSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec4[2];
	
  public:
	
	int getNumInputsGamelanSaronSIG0() {
		return 0;
	}
	int getNumOutputsGamelanSaronSIG0() {
		return 1;
	}
	
	void instanceInitGamelanSaronSIG0(int sample_rate) {
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iVec2[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iRec4[l6] = 0;
		}
	}
	
	void fillGamelanSaronSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec4[0] = (iVec2[1] + iRec4[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec4[0]));
			iVec2[1] = iVec2[0];
			iRec4[1] = iRec4[0];
		}
	}

};

static GamelanSaronSIG0* newGamelanSaronSIG0() { return (GamelanSaronSIG0*)new GamelanSaronSIG0(); }
static void deleteGamelanSaronSIG0(GamelanSaronSIG0* dsp) { delete dsp; }

static float GamelanSaron_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0GamelanSaronSIG0[65536];

class GamelanSaron : public dsp {
	
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
	FAUSTFLOAT fHslider2;
	float fConst10;
	float fRec5[2];
	int iRec6[2];
	float fConst11;
	float fRec7[2];
	FAUSTFLOAT fHslider3;
	float fConst12;
	float fConst13;
	float fRec8[2];
	float fConst14;
	float fConst15;
	float fConst16;
	float fRec9[2];
	float fConst17;
	float fConst18;
	float fRec10[2];
	float fRec11[2];
	float fRec12[2];
	FAUSTFLOAT fHslider4;
	float fConst19;
	float fRec13[2];
	float fRec14[2];
	float fConst20;
	FAUSTFLOAT fHslider5;
	float fRec0[3];
	
 public:
	GamelanSaron() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn GamelanSaron -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "gamelan_saron.dsp");
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
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "gamelan_saron");
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
		GamelanSaronSIG0* sig0 = newGamelanSaronSIG0();
		sig0->instanceInitGamelanSaronSIG0(sample_rate);
		sig0->fillGamelanSaronSIG0(65536, ftbl0GamelanSaronSIG0);
		deleteGamelanSaronSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(28274.334f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / GamelanSaron_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -1.4142135f) / fConst1 + 1.0f;
		fConst5 = 1.0f / ((fConst3 + 1.4142135f) / fConst1 + 1.0f);
		fConst6 = 9.424778f / fConst0;
		fConst7 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst8 = 1.0f / fConst7;
		fConst9 = 1.0f / std::max<float>(1.0f, 0.008f * fConst0);
		fConst10 = 8.93f / fConst0;
		fConst11 = 1.0f / std::max<float>(1.0f, 0.05f * fConst0);
		fConst12 = 0.18f * fConst0;
		fConst13 = 5.4f / fConst0;
		fConst14 = 1.0f / std::max<float>(1.0f, 0.08f * fConst0);
		fConst15 = 0.3f * fConst0;
		fConst16 = 2.76f / fConst0;
		fConst17 = 1.0f / std::max<float>(1.0f, 0.12f * fConst0);
		fConst18 = 0.55f * fConst0;
		fConst19 = 1.0f / fConst0;
		fConst20 = 1.0f / std::max<float>(1.0f, 0.2f * fConst0);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(293.66f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.3f);
		fHslider2 = FAUSTFLOAT(6.0f);
		fHslider3 = FAUSTFLOAT(1.6f);
		fHslider4 = FAUSTFLOAT(0.5f);
		fHslider5 = FAUSTFLOAT(0.45f);
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
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec5[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			iRec6[l8] = 0;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec7[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec8[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec9[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec10[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fRec11[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 2; l14 = l14 + 1) {
			fRec12[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 2; l15 = l15 + 1) {
			fRec13[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 2; l16 = l16 + 1) {
			fRec14[l16] = 0.0f;
		}
		for (int l17 = 0; l17 < 3; l17 = l17 + 1) {
			fRec0[l17] = 0.0f;
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
	
	virtual GamelanSaron* clone() {
		return new GamelanSaron();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("gamelan_saron");
		ui_interface->addHorizontalSlider("freq", &fHslider0, FAUSTFLOAT(293.66f), FAUSTFLOAT(4e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.45f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("ombak", &fHslider2, FAUSTFLOAT(6.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("ring", &fHslider3, FAUSTFLOAT(1.6f), FAUSTFLOAT(0.3f), FAUSTFLOAT(4.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("shimmer", &fHslider4, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("strike", &fHslider1, FAUSTFLOAT(0.3f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = std::tan(fConst6 * fSlow0);
		float fSlow2 = 2.0f * (1.0f - 1.0f / GamelanSaron_faustpower2_f(fSlow1));
		float fSlow3 = 1.0f / fSlow1;
		float fSlow4 = (fSlow3 + -0.5f) / fSlow1 + 1.0f;
		float fSlow5 = (fSlow3 + 0.5f) / fSlow1 + 1.0f;
		float fSlow6 = 1.0f / fSlow5;
		float fSlow7 = float(fButton0);
		float fSlow8 = 4.656613e-10f * float(fHslider1);
		float fSlow9 = 1.0f / (fSlow1 * fSlow5);
		float fSlow10 = fSlow0 + float(fHslider2);
		float fSlow11 = fConst10 * fSlow10;
		int iSlow12 = fSlow7 == 0.0f;
		float fSlow13 = float(fHslider3);
		float fSlow14 = 1.0f / std::max<float>(1.0f, fConst12 * fSlow13);
		float fSlow15 = fConst13 * fSlow10;
		float fSlow16 = 1.0f / std::max<float>(1.0f, fConst15 * fSlow13);
		float fSlow17 = fConst16 * fSlow10;
		float fSlow18 = 1.0f / std::max<float>(1.0f, fConst18 * fSlow13);
		float fSlow19 = fConst10 * fSlow0;
		float fSlow20 = fConst13 * fSlow0;
		float fSlow21 = fConst16 * fSlow0;
		float fSlow22 = float(fHslider4);
		float fSlow23 = fConst19 * fSlow10;
		float fSlow24 = fConst19 * fSlow0;
		float fSlow25 = 1.0f / std::max<float>(1.0f, fConst0 * fSlow13);
		float fSlow26 = 0.68f * float(fHslider5);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow7;
			iRec2[0] = (iRec2[1] + (iRec2[1] > 0)) * (fSlow7 <= fVec1[1]) + (fSlow7 > fVec1[1]);
			float fTemp0 = float(iRec2[0]);
			iRec3[0] = 1103515245 * iRec3[1] + 12345;
			fRec1[0] = fSlow8 * float(iRec3[0]) * std::max<float>(0.0f, std::min<float>(fConst8 * fTemp0, fConst9 * (fConst7 - fTemp0) + 1.0f)) - fSlow6 * (fSlow4 * fRec1[2] + fSlow2 * fRec1[1]);
			int iTemp1 = 1 - iVec0[1];
			float fTemp2 = ((iTemp1) ? 0.0f : fSlow11 + fRec5[1]);
			fRec5[0] = fTemp2 - std::floor(fTemp2);
			iRec6[0] = iSlow12 * (iRec6[1] + 1);
			float fTemp3 = float(iRec6[0]);
			fRec7[0] = fSlow7 + fRec7[1] * float(fVec1[1] >= fSlow7);
			float fTemp4 = fConst8 * fRec7[0];
			float fTemp5 = fConst7 - fRec7[0];
			float fTemp6 = std::max<float>(0.0f, std::min<float>(fTemp4, std::max<float>(fSlow14 * fTemp5 + 1.0f, 0.0f)) * (1.0f - fConst11 * fTemp3));
			float fTemp7 = ((iTemp1) ? 0.0f : fSlow15 + fRec8[1]);
			fRec8[0] = fTemp7 - std::floor(fTemp7);
			float fTemp8 = std::max<float>(0.0f, std::min<float>(fTemp4, std::max<float>(fSlow16 * fTemp5 + 1.0f, 0.0f)) * (1.0f - fConst14 * fTemp3));
			float fTemp9 = ((iTemp1) ? 0.0f : fSlow17 + fRec9[1]);
			fRec9[0] = fTemp9 - std::floor(fTemp9);
			float fTemp10 = std::max<float>(0.0f, std::min<float>(fTemp4, std::max<float>(fSlow18 * fTemp5 + 1.0f, 0.0f)) * (1.0f - fConst17 * fTemp3));
			float fTemp11 = ((iTemp1) ? 0.0f : fSlow19 + fRec10[1]);
			fRec10[0] = fTemp11 - std::floor(fTemp11);
			float fTemp12 = ((iTemp1) ? 0.0f : fSlow20 + fRec11[1]);
			fRec11[0] = fTemp12 - std::floor(fTemp12);
			float fTemp13 = ((iTemp1) ? 0.0f : fSlow21 + fRec12[1]);
			fRec12[0] = fTemp13 - std::floor(fTemp13);
			float fTemp14 = ((iTemp1) ? 0.0f : fSlow23 + fRec13[1]);
			fRec13[0] = fTemp14 - std::floor(fTemp14);
			float fTemp15 = ((iTemp1) ? 0.0f : fSlow24 + fRec14[1]);
			fRec14[0] = fTemp15 - std::floor(fTemp15);
			fRec0[0] = fSlow26 * (0.5f * (std::max<float>(0.0f, std::min<float>(fTemp4, std::max<float>(fSlow25 * fTemp5 + 1.0f, 0.0f)) * (1.0f - fConst20 * fTemp3)) * (ftbl0GamelanSaronSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec14[0]), 65535))] + ftbl0GamelanSaronSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec13[0]), 65535))]) + fSlow22 * (0.6f * ftbl0GamelanSaronSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec12[0]), 65535))] * fTemp10 + 0.35f * ftbl0GamelanSaronSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec11[0]), 65535))] * fTemp8 + 0.18f * ftbl0GamelanSaronSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec10[0]), 65535))] * fTemp6 + 0.6f * fTemp10 * ftbl0GamelanSaronSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec9[0]), 65535))] + 0.35f * fTemp8 * ftbl0GamelanSaronSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec8[0]), 65535))] + 0.18f * fTemp6 * ftbl0GamelanSaronSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec5[0]), 65535))])) + fSlow9 * (fRec1[0] - fRec1[2])) - fConst5 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			float fTemp16 = fConst5 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp16);
			output1[i0] = FAUSTFLOAT(fTemp16);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec2[1] = iRec2[0];
			iRec3[1] = iRec3[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec5[1] = fRec5[0];
			iRec6[1] = iRec6[0];
			fRec7[1] = fRec7[0];
			fRec8[1] = fRec8[0];
			fRec9[1] = fRec9[0];
			fRec10[1] = fRec10[0];
			fRec11[1] = fRec11[0];
			fRec12[1] = fRec12[0];
			fRec13[1] = fRec13[0];
			fRec14[1] = fRec14[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
